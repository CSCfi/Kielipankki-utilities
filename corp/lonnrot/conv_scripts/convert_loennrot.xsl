<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8" omit-xml-declaration="yes"/>

  <xsl:variable name="reference" select="document('lonnrot-xml-showlink-map-20191002.xml')/references"/>
  
  <xsl:template match="*">
    <xsl:copy>
      <xsl:for-each select="@*">
        <xsl:copy/>
      </xsl:for-each>
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>
  
  <!-- Sort the works after addressee and by date -->
  <xsl:template match="letters">
    <letters>
      <xsl:apply-templates>
	<xsl:sort select="teiHeader/fileDesc/sourceDesc//title/surname"/>
	<xsl:sort select="teiHeader/fileDesc/sourceDesc//title/forename"/>
	<xsl:sort select="text//date/@when"/>
      </xsl:apply-templates>
    </letters>
  </xsl:template>

  <xsl:template match="letter">
    <!--<xsl:call-template name="text"/>-->
    <xsl:variable name="filename" select="@name"/>
  <xsl:element name="text_new">
      <xsl:attribute name="title"><xsl:value-of select="teiHeader/fileDesc/titleStmt/title"/></xsl:attribute>
      <!--<xsl:attribute name="author"><xsl:value-of select="teiHeader/fileDesc/titleStmt/author"/></xsl:attribute>-->
      <xsl:attribute name="filename"><xsl:value-of select="@name"/></xsl:attribute>
      <xsl:attribute name="source_xml"><xsl:text>http://lonnrot.finlit.fi/omeka/uploads/</xsl:text><xsl:value-of select="@name"/></xsl:attribute>
      <xsl:attribute name="show"><xsl:value-of select="$reference/ref[file=$filename]/address"/></xsl:attribute>
      <xsl:attribute name="edition"><xsl:value-of select="teiHeader/fileDesc/editionStmt/edition"/></xsl:attribute>
      <xsl:attribute name="distributor"><xsl:value-of select="teiHeader/fileDesc/publicationStmt/distributor"/></xsl:attribute>
      <xsl:attribute name="published"><xsl:value-of select="teiHeader/fileDesc/publicationStmt/date/@when"/></xsl:attribute>
      <xsl:attribute name="repository"><xsl:value-of select="teiHeader/fileDesc/sourceDesc//repository"/></xsl:attribute>
      <xsl:attribute name="idno"><xsl:value-of select="teiHeader/fileDesc/sourceDesc//idno"/></xsl:attribute>
      <xsl:attribute name="item_class"><xsl:value-of select="teiHeader/fileDesc/sourceDesc/msDesc/msContents/msItem/@class"/></xsl:attribute>
      <xsl:attribute name="author"><xsl:value-of select="teiHeader/fileDesc/sourceDesc//author/surname"/>, <xsl:value-of select="teiHeader/fileDesc/sourceDesc//author/forename"/></xsl:attribute>
      <!--<xsl:attribute name="addressee"><xsl:value-of select="teiHeader/fileDesc/sourceDesc//title[@type='adressee']/surname"/>, <xsl:value-of select="teiHeader/fileDesc/sourceDesc//title[@type='adressee']/forename"/></xsl:attribute>-->
      <xsl:attribute name="addressee">
	<xsl:choose>
	  <xsl:when test="teiHeader/fileDesc/sourceDesc//bibl='254'">Bergbom, Gustaf</xsl:when>
	  <xsl:when test="teiHeader/fileDesc/sourceDesc//bibl='358'">Calamnius, Fredrik</xsl:when>
	  <xsl:when test="teiHeader/fileDesc/sourceDesc//bibl='705'">Lindholm</xsl:when>
	  <xsl:when test="teiHeader/fileDesc/sourceDesc//bibl='2772'">Piponius, Jakobina</xsl:when>
	  <xsl:otherwise>
	    <xsl:value-of select="teiHeader/fileDesc/sourceDesc//title[@type='adressee']/surname"/>, <xsl:value-of select="teiHeader/fileDesc/sourceDesc//title[@type='adressee']/forename"/>
	  </xsl:otherwise>
	</xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="bibl"><xsl:value-of select="teiHeader/fileDesc/sourceDesc//bibl"/></xsl:attribute>
      <xsl:attribute name="lang"><xsl:value-of select="teiHeader/profileDesc//language"/></xsl:attribute>
      <xsl:attribute name="langs"><xsl:text>|</xsl:text><xsl:for-each select="teiHeader/profileDesc//language"><xsl:value-of select="@ident"/><xsl:text>:</xsl:text><xsl:value-of select="@usage"/><xsl:text>|</xsl:text></xsl:for-each></xsl:attribute>
      <xsl:attribute name="div_type"><xsl:value-of select="text/body/div/@type"/></xsl:attribute>
      <xsl:attribute name="place_name"><xsl:value-of select="text//placeName"/></xsl:attribute>
     <xsl:attribute name="date"><xsl:value-of select="text//date"/></xsl:attribute>
      <xsl:attribute name="year"><xsl:value-of select="text//date/@when"/></xsl:attribute>
     <xsl:attribute name="relation_to"><xsl:value-of select="text//rs/@relation_to"/></xsl:attribute>
     <xsl:attribute name="relation_type"><xsl:value-of select="text//rs/@relation_type"/></xsl:attribute>
      <xsl:attribute name="datefrom"><xsl:value-of select="text//date/@when"/></xsl:attribute>
      <xsl:attribute name="dateto"><xsl:value-of select="text//date/@when"/></xsl:attribute>
      <xsl:attribute name="timefrom">000000</xsl:attribute>
      <xsl:attribute name="timeto">235959</xsl:attribute>
    <xsl:apply-templates/>
   </xsl:element>
  </xsl:template>


  <xsl:template match="teiHeader"/>


  <xsl:template match="text">
    <xsl:apply-templates/>
  </xsl:template>
  
  <xsl:template match="body">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="div">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="opener"/>

  <xsl:template match="emph"/>

  <!-- rename p to paragraph -->
  <!--<xsl:template match="p">
    <paragraph>
      <xsl:apply-templates/>
    </paragraph>
  </xsl:template>-->

  <xsl:template match="p">
    <xsl:choose>
      <xsl:when test="./rs">
	<paragraph type="editor_note">
	  <xsl:apply-templates/>
	</paragraph>
      </xsl:when>
      <xsl:otherwise>
	<paragraph type="">
	  <xsl:apply-templates/>
	</paragraph>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--<xsl:template match="gap">
    <xsl:text>&lt;gap&gt;</xsl:text>
  </xsl:template>-->

  <xsl:template match="rs">
    <xsl:apply-templates/>
  </xsl:template>

  
   <!-- surround table with paragraph -->
   <xsl:template match="table">
     <xsl:choose>
       <xsl:when test="ancestor::paragraph">
	 <table>
	   <xsl:apply-templates/>
	 </table>
       </xsl:when>
       <xsl:otherwise>
	 <paragraph type="">
	   <table>
	     <xsl:apply-templates/>
	   </table>
	 </paragraph>
       </xsl:otherwise>
     </xsl:choose>
   </xsl:template>


 <!-- <xsl:template match="row">
    <div type="table_row">
      <xsl:apply-templates/>
    </div>
  </xsl:template>-->

  <!--<xsl:template match="cell">
    <span type="table_cell">
      <xsl:apply-templates/>
    </span>
  </xsl:template>-->


  <!-- ref and notes -->
  <!--<xsl:template match="ref">
    <span type="editor_note">
      <xsl:apply-templates/>
    </span>
  </xsl:template>-->

  <xsl:template match="ref">
    <xsl:element name="span">
      <xsl:attribute name="type">editor_note</xsl:attribute>
      <xsl:attribute name="text"><xsl:value-of select="note"/></xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="note"/>


  <xsl:template match="square_bracket">
    <xsl:element name="span">
      <xsl:attribute name="type">editor_note</xsl:attribute>
      <xsl:attribute name="text"><xsl:value-of select="."/></xsl:attribute>
      <xsl:text>&#xA0;</xsl:text>
    </xsl:element>
  </xsl:template>

  <xsl:template match="unclear">
    <span type="unclear" text="">
      <xsl:apply-templates/>
    </span>
  </xsl:template>

  <xsl:template match="lg">
    <xsl:choose>
      <xsl:when test="ancestor::table">
	<linegroup>
	  <xsl:apply-templates/>
	</linegroup>
      </xsl:when>
      <xsl:otherwise>
	<paragraph type="">
	  <linegroup>
	    <xsl:apply-templates/>
	  </linegroup>
	</paragraph>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
    <xsl:template match="l">
      <line>
	<xsl:apply-templates/>
      </line>
    </xsl:template>

  <xsl:template match="add">
    <correction type="addition" orig="">
      <xsl:apply-templates/>
    </correction>
  </xsl:template>

  <!--<xsl:template match="del">
    <correction type="deletion">
      <xsl:apply-templates/>
    </correction>
  </xsl:template>-->

  <xsl:template match="del">
    <xsl:element name="correction">
      <xsl:attribute name="type">deletion</xsl:attribute>
      <xsl:attribute name="orig"><xsl:value-of select="."/></xsl:attribute>
      <xsl:text>&#xA0;</xsl:text>
    </xsl:element>
  </xsl:template>

 <!-- <xsl:template match="app">
    <alternatives>
      <xsl:apply-templates/>
    </alternatives>
  </xsl:template>

  <xsl:template match="lem">
    <alternative type="lem">
      <xsl:apply-templates/>
    </alternative>
  </xsl:template>
  
  <xsl:template match="rdg">
    <alternative type="rdg">
      <xsl:apply-templates/>
    </alternative>
  </xsl:template>
-->

 <xsl:template match="app">
   <xsl:element name="alternative">
     <xsl:attribute name="text"><xsl:value-of select="rdg"/></xsl:attribute>
     <xsl:apply-templates/>
   </xsl:element>
 </xsl:template>

 <xsl:template match="lem">
   <xsl:apply-templates/>
 </xsl:template>
 
 <xsl:template match="rdg"/>

 <xsl:template match="ptr">
   <xsl:element name="span">
     <xsl:attribute name="type">ext_link</xsl:attribute>
     <xsl:attribute name="text"><xsl:value-of select="@target"/></xsl:attribute>
     <xsl:apply-templates/>
   </xsl:element>
 </xsl:template>
 
</xsl:stylesheet>
